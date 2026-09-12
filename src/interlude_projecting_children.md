# การโปรเจกต์ children

ขณะที่คุณสร้างคอมโพเนนต์ คุณอาจพบว่าตัวเองต้องการ “โปรเจกต์” ลูก (children) ผ่านคอมโพเนนต์หลายชั้น

## ปัญหา

ลองพิจารณาโค้ดต่อไปนี้:

```rust
pub fn NestedShow<F, IV>(fallback: F, children: ChildrenFn) -> impl IntoView
where
    F: Fn() -> IV + Send + Sync + 'static,
    IV: IntoView + 'static,
{
    view! {
        <Show
            when=|| todo!()
            fallback=|| ()
        >
            <Show
                when=|| todo!()
                fallback=fallback
            >
                {children()}
            </Show>
        </Show>
    }
}
```

เรื่องนี้ค่อนข้างตรงไปตรงมา: หากเงื่อนไขชั้นในเป็น `true` เราต้องการแสดง `children` หากไม่ใช่ เราต้องการแสดง `fallback` และหากเงื่อนไขชั้นนอกเป็น `false` เราก็แค่เรนเดอร์ `()` นั่นคือ ไม่มีอะไรเลย

พูดอีกอย่างคือ เราต้องการส่ง children ของ `<NestedShow/>` _ผ่าน_ คอมโพเนนต์ `<Show/>` ชั้นนอก เพื่อให้กลายเป็น children ของ `<Show/>` ชั้นใน นี่คือสิ่งที่ผมหมายถึงคำว่า “การโปรเจกต์”

โค้ดนี้จะคอมไพล์ไม่ผ่าน

```
error[E0525]: expected a closure that implements the `Fn` trait, but this closure only implements `FnOnce`
```

แต่ละ `<Show/>` ต้องสามารถสร้าง `children` ของตัวเองได้หลายครั้ง ครั้งแรกที่คุณสร้าง children ของ `<Show/>` ชั้นนอก มันจะนำ `fallback` และ `children` ไปเคลื่อนย้ายเข้าไปในการเรียกใช้ `<Show/>` ชั้นใน แต่หลังจากนั้น พวกมันก็ใช้ไม่ได้อีกสำหรับการสร้าง children ของ `<Show/>` ชั้นนอกในครั้งต่อๆ ไป

## รายละเอียด

> เชิญข้ามไปยังวิธีแก้ปัญหากันได้เลย

หากคุณอยากเข้าใจปัญหานี้อย่างแท้จริง การดูมาโคร `view` ที่ถูกขยายออกมาอาจช่วยได้ นี่คือเวอร์ชันที่จัดระเบียบใหม่แล้ว:

```rust
Show(
    ShowProps::builder()
        .when(|| todo!())
        .fallback(|| ())
        .children({
            // children and fallback are moved into a closure here
            ::leptos::children::ToChildren::to_children(move || {
                Show(
                    ShowProps::builder()
                        .when(|| todo!())
                        // fallback is consumed here
                        .fallback(fallback)
                        .children({
                            // children is captured here
                            ::leptos::children::ToChildren::to_children(
                                move || children(),
                            )
                        })
                        .build(),
                )
            })
        })
        .build(),
)
```

คอมโพเนนต์ทุกตัวเป็นเจ้าของพร็อพของมัน ดังนั้น `<Show/>` ในกรณีนี้จึงเรียกใช้ไม่ได้ เพราะมันมีเพียงรีเฟอเรนซ์ที่แคปเจอร์ไว้ไปยัง `fallback` และ `children`

## วิธีแก้ปัญหา

อย่างไรก็ตาม ทั้ง `<Suspense/>` และ `<Show/>` รับ `ChildrenFn` กล่าวคือ `children` ของพวกมันควรอิมพลีเมนต์ชนิด `Fn` เพื่อให้เรียกใช้ได้หลายครั้งด้วยรีเฟอเรนซ์แบบไม่เปลี่ยนค่าเท่านั้น ซึ่งหมายความว่าเราไม่จำเป็นต้องเป็นเจ้าของ `children` หรือ `fallback` เราแค่ต้องสามารถส่งรีเฟอเรนซ์ `'static` ไปยังพวกมันได้

เราแก้ปัญหานี้ได้โดยใช้พริมิทีฟ [`StoredValue`](https://docs.rs/leptos/latest/leptos/reactive/owner/struct.StoredValue.html) ซึ่งโดยพื้นฐานแล้วจะเก็บค่าไว้ในระบบรีแอกทีฟ โดยยกความเป็นเจ้าของให้กับเฟรมเวิร์ก เพื่อแลกกับรีเฟอเรนซ์ที่เหมือนสัญญาณ กล่าวคือเป็น `Copy` และ `'static` ซึ่งเราเข้าถึงหรือแก้ไขมันได้ผ่านเมธอดบางอย่าง

ในกรณีนี้ มันง่ายมาก:

```rust
pub fn NestedShow<F, IV>(fallback: F, children: ChildrenFn) -> impl IntoView
where
    F: Fn() -> IV + Send + Sync + 'static,
    IV: IntoView + 'static,
{
    let fallback = StoredValue::new(fallback);
    let children = StoredValue::new(children);

    view! {
        <Show
            when=|| todo!()
            fallback=|| ()
        >
            <Show
                // check whether user is verified
                // by reading from the resource
                when=move || todo!()
                fallback=move || fallback.read_value()()
            >
                {children.read_value()()}
            </Show>
        </Show>
    }
}
```

ที่ระดับบนสุด เราเก็บทั้ง `fallback` และ `children` ไว้ในสโคปแบบรีแอกทีฟที่เป็นของ `NestedShow` ตอนนี้เราเพียงเคลื่อนย้ายรีเฟอเรนซ์เหล่านั้นลงผ่านชั้นอื่นๆ เข้าไปในคอมโพเนนต์ `<Show/>` แล้วเรียกใช้พวกมันที่นั่น

## บันทึกสุดท้าย

โปรดทราบว่าวิธีนี้ใช้ได้เพราะ `<Show/>` ต้องการเพียงรีเฟอเรนซ์แบบไม่เปลี่ยนค่าไปยัง children ของมัน (ซึ่ง `.read_value` มอบให้ได้) ไม่ใช่ความเป็นเจ้าของ

ในกรณีอื่นๆ คุณอาจต้องโปรเจกต์พร็อพที่เป็นเจ้าของผ่านฟังก์ชันที่รับ `ChildrenFn` และดังนั้นจึงต้องถูกเรียกใช้มากกว่าหนึ่งครั้ง ในกรณีนี้ คุณอาจพบว่าตัวช่วย `clone:` ในมาโคร `view` มีประโยชน์

ลองพิจารณาตัวอย่างนี้

```rust
#[component]
pub fn App() -> impl IntoView {
    let name = "Alice".to_string();
    view! {
        <Outer>
            <Inner>
                <Inmost name=name.clone()/>
            </Inner>
        </Outer>
    }
}

#[component]
pub fn Outer(children: ChildrenFn) -> impl IntoView {
    children()
}

#[component]
pub fn Inner(children: ChildrenFn) -> impl IntoView {
    children()
}

#[component]
pub fn Inmost(name: String) -> impl IntoView {
    view! {
        <p>{name}</p>
    }
}
```

แม้จะใช้ `name=name.clone()` ก็ยังให้ข้อผิดพลาด

```
cannot move out of `name`, a captured variable in an `Fn` closure
```

มันถูกแคปเจอร์ผ่าน children หลายชั้นที่ต้องรันมากกว่าหนึ่งครั้ง และไม่มีวิธีที่ชัดเจนในการโคลนมัน _เข้าไปใน_ children

ในกรณีนี้ ไวยากรณ์ `clone:` มีประโยชน์มาก การเรียก `clone:name` จะโคลน `name` _ก่อน_ ที่จะเคลื่อนย้ายมันเข้าไปใน children ของ `<Inner/>` ซึ่งแก้ปัญหาความเป็นเจ้าของของเราได้

```rust
view! {
	<Outer>
		<Inner clone:name>
			<Inmost name=name.clone()/>
		</Inner>
	</Outer>
}
```

ปัญหาเหล่านี้อาจเข้าใจหรือดีบักได้ยากสักหน่อย เนื่องจากความไม่โปร่งใสของมาโคร `view` แต่โดยทั่วไปแล้ว พวกมันแก้ไขได้เสมอ
