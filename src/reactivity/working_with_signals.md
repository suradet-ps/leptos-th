# การทำงานกับสัญญาณ

จนถึงตอนนี้ เราได้เห็นตัวอย่างพื้นฐานของการใช้งานฟังก์ชัน [`signal`](https://docs.rs/leptos/latest/leptos/reactive/signal/fn.signal.html) ซึ่งจะคืนค่าออกมาเป็นตัวอ่านข้อมูล (getter) ในรูปของ [`ReadSignal`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.ReadSignal.html) และตัวเขียนข้อมูล (setter) ในรูปของ [`WriteSignal`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.WriteSignal.html)

## การอ่านค่าและการตั้งค่า

การดำเนินการพื้นฐานกับสัญญาณมีอยู่ไม่กี่รูปแบบ ดังนี้:

### การอ่านค่า

1. [`.read()`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.ReadSignal.html#impl-Read-for-T) คืนค่าเป็น read guard ที่สามารถ dereference ไปยังค่าของสัญญาณได้โดยตรง และจะคอยติดตาม (track) การเปลี่ยนแปลงของสัญญาณในอนาคตแบบรีแอกทีฟ ทั้งนี้ คุณจะไม่สามารถอัปเดตค่าของสัญญาณได้จนกว่า guard นี้จะถูก drop ออกไป ไม่เช่นนั้นจะเกิดข้อผิดพลาดขึ้นในขณะรันไทม์ (panic)
1. [`.with()`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.ReadSignal.html#impl-With-for-T) รับฟังก์ชันคลอเชอร์ที่จะได้รับค่าปัจจุบันของสัญญาณในแบบการอ้างอิง (`&T`) พร้อมทั้งคอยติดตามสัญญาณนั้นให้โดยอัตโนมัติ
1. [`.get()`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.ReadSignal.html#impl-Get-for-T) โคลน (clone) ค่าปัจจุบันของสัญญาณออกมา และติดตามการเปลี่ยนแปลงของค่านั้นต่อไป

`.get()` เป็นเมธอดที่นิยมใช้งานบ่อยที่สุดในการเข้าถึงค่าของสัญญาณ ส่วน `.read()` จะมีประโยชน์มากสำหรับเมธอดที่ต้องการเพียงการอ้างอิงแบบไม่เปลี่ยนแปลงค่า (immutable reference) โดยไม่ต้องเสียต้นทุนในการโคลนข้อมูล (เช่น `my_vec_signal.read().len()`) และสำหรับ `.with()` จะเหมาะเมื่อคุณต้องการประมวลผลข้อมูลผ่านการอ้างอิงนั้นเพิ่มเติม แต่ต้องการความมั่นใจว่าจะไม่ถือ lock ค้างไว้นานเกินความจำเป็น

### การตั้งค่า

1. [`.write()`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.WriteSignal.html#impl-Write-for-WriteSignal%3CT,+S%3E) คืนค่าเป็น write guard ซึ่งเป็นการอ้างอิงแบบเปลี่ยนแปลงค่าได้ (`&mut T`) ไปยังค่าภายในของสัญญาณ พร้อมแจ้งเตือนผู้ติดตาม (subscribers) ทั้งหมดว่าต้องอัปเดต ทั้งนี้ คุณจะไม่สามารถอ่านค่าของสัญญาณได้จนกว่า guard นี้จะถูก drop ไม่เช่นนั้นจะเกิดข้อผิดพลาดในขณะรันไทม์
1. [`.update()`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.WriteSignal.html#impl-Update-for-T) รับฟังก์ชันคลอเชอร์ที่จะได้รับ mutable reference ไปยังค่าปัจจุบันของสัญญาณ (`&mut T`) แล้วแจ้งเตือนผู้ติดตาม (ทั้งนี้ `.update()` จะไม่คืนค่าที่คลอเชอร์ส่งกลับมา แต่คุณสามารถใช้ [`.try_update()`](https://docs.rs/leptos/latest/leptos/trait.SignalUpdate.html#tymethod.try_update) แทนได้หากต้องการ เช่น เมื่อคุณสั่งลบสมาชิกออกจาก `Vec<_>` และต้องการนำสมาชิกที่ถูกลบนั้นออกมาใช้งานต่อ)
1. [`.set()`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.WriteSignal.html#impl-Set-for-T) แทนที่ค่าเดิมของสัญญาณด้วยค่าใหม่ทั้งหมด และแจ้งเตือนผู้ติดตามทันที

`.set()` เป็นวิธีที่นิยมใช้มากที่สุดในการกำหนดค่าใหม่ ส่วน `.write()` มีประโยชน์อย่างยิ่งสำหรับการอัปเดตข้อมูลเดิมโดยตรงในหน่วยความจำ (in place) และเช่นเดียวกับกรณีของ `.read()` กับ `.with()` เมธอด `.update()` จะช่วยให้คุณมั่นใจได้ว่าจะไม่เผลอถือ write lock ค้างไว้นานเกินกว่าที่ตั้งใจไว้

```admonish note
เทรต (trait) เหล่านี้ถูกสร้างขึ้นจากการประกอบกันของเทรตย่อย ๆ (trait composition) และมีการอิมพลีเมนต์แบบครอบคลุม (blanket implementations) มาให้ ตัวอย่างเช่น `Read` จะถูกอิมพลีเมนต์ให้กับทุกชนิดข้อมูลที่อิมพลีเมนต์ `Track` และ `ReadUntracked` ส่วน `With` จะถูกอิมพลีเมนต์ให้กับชนิดข้อมูลใดก็ตามที่อิมพลีเมนต์ `Read` และ `Get` ก็จะถูกอิมพลีเมนต์ให้กับชนิดข้อมูลใดก็ตามที่อิมพลีเมนต์ทั้ง `With` และ `Clone` เป็นต้น

ความสัมพันธ์ในลักษณะเดียวกันนี้ก็มีอยู่สำหรับกลุ่มของ `Write`, `Update` และ `Set` ด้วยเช่นกัน

ประเด็นนี้มีประโยชน์อย่างยิ่งเมื่อคุณอ่านเอกสารอ้างอิงของ API: แม้คุณจะเห็นว่าเอกสารระบุไว้เพียงเทรต `ReadUntracked` และ `Track` เท่านั้น คุณก็ยังคงสามารถเรียกใช้ `.with()`, `.get()` (ตราบใดที่ `T: Clone`) และเมธอดอื่น ๆ ได้ตามปกติ
```

## การทำงานกับสัญญาณ

คุณอาจสังเกตเห็นว่า อันที่จริง `.get()` และ `.set()` สามารถเขียนขึ้นมาจาก `.read()` และ `.write()` หรือ `.with()` และ `.update()` ได้ กล่าวอีกนัยหนึ่งคือ `count.get()` ให้ผลลัพธ์เหมือนกับการเขียน `count.with(|n| n.clone())` หรือ `count.read().clone()` และ `count.set(1)` ก็ทำงานเทียบเท่ากับการเขียน `count.update(|n| *n = 1)` หรือ `*count.write() = 1`

แต่แน่นอนว่า ไวยากรณ์ของ `.get()` และ `.set()` นั้นดูเรียบง่ายและอ่านสบายตากว่ามาก

อย่างไรก็ตาม เมธอดอื่น ๆ ก็มีกรณีการใช้งานเฉพาะตัวที่สำคัญไม่แพ้กัน

ตัวอย่างเช่น ลองพิจารณาสัญญาณที่เก็บข้อมูลประเภท `Vec<String>`:

```rust
let (names, set_names) = signal(Vec::new());
if names.get().is_empty() {
	set_names(vec!["Alice".to_string()]);
}
```

ในแง่ของตรรกะ โค้ดนี้ดูเรียบง่ายตรงไปตรงมา แต่มันแฝงความไร้ประสิทธิภาพที่สำคัญเอาไว้ อย่าลืมว่า `names.get().is_empty()` จะทำการโคลนค่าออกมา นั่นหมายความว่าเรากำลังโคลน `Vec<String>` ทั้งก้อนขึ้นมาใหม่ เพียงเพื่อเรียกเมธอด `is_empty()` แล้วโยนข้อมูลที่โคลนมานั้นทิ้งไปทันที

ในทำนองเดียวกัน `set_names` ก็นำ `Vec<_>` ก้อนใหม่ทั้งก้อนไปแทนที่ค่าเดิม ซึ่งแม้จะทำงานได้ แต่คงจะดีกว่ามากหากเราสามารถแก้ไขค่า (mutate) ภายใน `Vec<_>` เดิมโดยตรงในตำแหน่งเดิม (in place):

```rust
let (names, set_names) = signal(Vec::new());
if names.read().is_empty() {
	set_names.write().push("Alice".to_string());
}
```

ในตอนนี้ โค้ดของเราจะเข้าถึง `names` ผ่านการอ้างอิงเพื่อเรียกใช้ `is_empty()` ทำให้ไม่ต้องเสียทรัพยากรไปกับการโคลน และสั่งเพิ่มข้อมูลลงใน `Vec<_>` เดิมได้ทันที

## ความปลอดภัยของเธรดและค่าประจำเธรด

คุณอาจสังเกตเห็น ไม่ว่าจะจากการอ่านเอกสารหรือจากการทดลองพัฒนาแอปพลิเคชันของคุณเอง ว่าค่าที่นำมาเก็บไว้ในสัญญาณจะต้องเป็นไปตามเงื่อนไข `Send + Sync` สาเหตุเป็นเพราะระบบรีแอกทีฟของ Leptos รองรับการทำงานแบบหลายเธรด (multithreading) อย่างแท้จริง สัญญาณสามารถถูกส่งข้ามเธรดได้ และโครงข่ายกราฟรีแอกทิวิตีทั้งหมดก็สามารถทำงานข้ามหลายเธรดได้เช่นกัน (สิ่งนี้มีประโยชน์อย่างยิ่งเมื่อทำ[การเรนเดอร์ฝั่งเซิร์ฟเวอร์ (SSR)](../ssr/) ร่วมกับเฟรมเวิร์กเซิร์ฟเวอร์อย่าง Axum ซึ่งทำงานบนรันไทม์แบบหลายเธรดของ Tokio) ในกรณีส่วนใหญ่ เงื่อนไขนี้จะไม่ส่งผลต่อการเขียนโค้ดของคุณ เพราะชนิดข้อมูลมาตรฐานในภาษา Rust ล้วนเป็น `Send + Sync` อยู่แล้วเป็นค่าเริ่มต้น

อย่างไรก็ตาม สภาพแวดล้อมการทำงานของเว็บเบราว์เซอร์นั้นเป็นแบบเธรดเดียว (single-threaded) เสมอ (เว้นแต่คุณจะใช้งาน Web Worker) และชนิดข้อมูลต่าง ๆ ของ JavaScript ที่ได้รับมาจาก `wasm-bindgen` หรือ `web-sys` ก็ถูกกำหนดไว้อย่างชัดเจนว่าไม่ปลอดภัยต่อการส่งข้ามเธรด (`!Send`) ซึ่งส่งผลให้ไม่สามารถนำไปเก็บไว้ในสัญญาณแบบปกติได้โดยตรง

ด้วยเหตุนี้ เราจึงมีพรีมิทีฟของสัญญาณรูปแบบ "local" เตรียมไว้ให้สำหรับแต่ละชนิด ซึ่งช่วยให้สามารถเก็บข้อมูลที่เป็น `!Send` ได้ ทั้งนี้ คุณควรเลือกใช้ตัวเลือกกลุ่มนี้เฉพาะเมื่อจำเป็นต้องเก็บชนิดข้อมูลของเบราว์เซอร์ที่เป็น `!Send` ไว้ในสัญญาณเท่านั้น:

| มาตรฐาน | โลคอล |
| -------- | ----- |
| [`signal`](https://docs.rs/leptos/latest/leptos/reactive/signal/fn.signal.html) | [`signal_local`](https://docs.rs/leptos/latest/leptos/prelude/fn.signal_local.html) |
| [`RwSignal::new`](https://docs.rs/leptos/latest/leptos/prelude/struct.RwSignal.html#method.new) | [`RwSignal::new_local`](https://docs.rs/leptos/latest/leptos/prelude/struct.RwSignal.html#method.new_local) |
| [`Resource`](https://docs.rs/leptos/latest/leptos/prelude/struct.Resource.html) | [`LocalResource`](https://docs.rs/leptos/latest/leptos/prelude/struct.LocalResource.html) |
| [`Action::new`](https://docs.rs/leptos/latest/leptos/prelude/struct.Action.html#method.new) | [`Action::new_local`](https://docs.rs/leptos/latest/leptos/prelude/struct.Action.html#method.new_local), [`Action::new_unsync`](https://docs.rs/leptos/latest/leptos/prelude/struct.Action.html#method.new_unsync) |

## ไวยากรณ์ nightly

เมื่อเปิดใช้งานฟีเจอร์ `nightly` ร่วมกับคอมไพเลอร์ Rust เวอร์ชัน nightly การเรียกใช้ `ReadSignal` ในรูปของฟังก์ชันจะทำหน้าที่เป็นไวยากรณ์แบบย่อ (syntax sugar) ของการเรียก `.get()` และการเรียก `WriteSignal` ในรูปของฟังก์ชันก็จะเป็น syntax sugar ของการเรียก `.set()` ดังนั้น:

```rust
let (count, set_count) = signal(0);
set_count(1);
logging::log!(count());
```

จึงมีความหมายเทียบเท่ากับ:

```rust
let (count, set_count) = signal(0);
set_count.set(1);
logging::log!(count.get());
```

สิ่งนี้ไม่ได้เป็นเพียงแค่ syntax sugar เท่านั้น แต่ยังช่วยให้รูปแบบ API มีความสอดคล้องกันมากขึ้น โดยทำให้สัญญาณมีลักษณะการทำงานเชิงความหมายที่ตรงกับฟังก์ชันอย่างแท้จริง: ดูเพิ่มเติมได้ที่[บทแทรกคั่นรายการ: รีแอกทิวิตีและฟังก์ชัน](./interlude_functions.md)

## การทำให้สัญญาณขึ้นต่อกัน

บ่อยครั้งที่มักมีคำถามเกี่ยวกับสถานการณ์ที่สัญญาณหนึ่งจำเป็นต้องเปลี่ยนค่าตามอีกสัญญาณหนึ่ง มี 3 วิธีการที่ดีในการจัดการกับเรื่องนี้ และอีก 1 วิธีที่แม้จะไม่ใช่วิธีในอุดมคติ แต่ก็ยอมรับได้ในสถานการณ์ที่มีการควบคุมอย่างรัดกุม:

### ทางเลือกที่ดี

**1) B เป็นฟังก์ชันของ A** ให้สร้างสัญญาณสำหรับ A ขึ้นมา และสร้างเป็นสัญญาณอนุพัทธ์ (derived signal) หรือ memo สำหรับ B:

```rust
// A
let (count, set_count) = signal(1);
// B is a function of A
let derived_signal_double_count = move || count.get() * 2;
// B is a function of A
let memoized_double_count = Memo::new(move |_| count.get() * 2);
```

> สำหรับคำแนะนำในการเลือกระหว่าง derived signal กับ memo สามารถดูเพิ่มเติมได้ที่เอกสารของ [`Memo`](https://docs.rs/leptos/latest/leptos/reactive/computed/struct.Memo.html)

**2) C เป็นฟังก์ชันของ A ร่วมกับข้อมูลอื่น B** ให้สร้างสัญญาณสำหรับ A และ B แยกกัน แล้วสร้าง derived signal หรือ memo สำหรับ C:

```rust
// A
let (first_name, set_first_name) = signal("Bridget".to_string());
// B
let (last_name, set_last_name) = signal("Jones".to_string());
// C is a function of A and B
let full_name = move || format!("{} {}", &*first_name.read(), &*last_name.read());
```

**3) A และ B เป็นสัญญาณที่เป็นอิสระต่อกัน แต่มีบางจังหวะที่ต้องอัปเดตพร้อมกัน** เมื่อคุณเขียนคำสั่งอัปเดตค่า A ก็ให้เขียนคำสั่งอัปเดตค่า B แยกต่างหากในคราวเดียวกัน:

```rust
// A
let (age, set_age) = signal(32);
// B
let (favorite_number, set_favorite_number) = signal(42);
// use this to handle a click on a `Clear` button
let clear_handler = move |_| {
  // update both A and B
  set_age.set(0);
  set_favorite_number.set(0);
};
```

### ถ้าคุณจำเป็นจริง ๆ...

**4) สร้างเอฟเฟกต์เพื่อเขียนค่าลงใน B ทุกครั้งที่ A เปลี่ยนแปลง** วิธีนี้เป็นแนวทางที่ไม่แนะนำอย่างเป็นทางการ ด้วยเหตุผลหลายประการ:
a) มันจะมีประสิทธิภาพด้อยกว่าเสมอ เพราะทุกครั้งที่ A มีการอัปเดต ระบบจะต้องวนรอบประมวลผลกระบวนการรีแอกทีฟถึง 2 รอบเต็ม ๆ (เริ่มจากคุณตั้งค่า A ซึ่งส่งผลให้เอฟเฟกต์รัน รวมถึงเอฟเฟกต์อื่น ๆ ที่ขึ้นกับ A จากนั้นคุณไปตั้งค่า B ซึ่งก็ไปกระตุ้นให้เอฟเฟกต์อื่น ๆ ที่ขึ้นกับ B ต้องรันซ้ำอีกรอบ)
b) มันเพิ่มความเสี่ยงที่จะเกิดข้อผิดพลาดร้ายแรงโดยไม่ตั้งใจ เช่น ลูปอนันต์ (infinite loop) หรือการสั่งรันเอฟเฟกต์ซ้ำซ้อนเกินความจำเป็น นี่คือรูปแบบของโค้ดรีแอกทีฟที่ตีลูกปิงปองไปมาจนกลายเป็น spaghetti code ที่มักพบเห็นได้บ่อยในยุคต้นทศวรรษ 2010 ซึ่งเป็นสิ่งที่เราพยายามหลีกเลี่ยงผ่านการออกแบบระบบ เช่น การแยกส่วนการอ่านและการเขียนออกจากกันอย่างชัดเจน และการไม่สนับสนุนให้เขียนอัปเดตค่าสัญญาณจากภายในเอฟเฟกต์

ในสถานการณ์ส่วนใหญ่ ทางออกที่ดีที่สุดคือการปรับโครงสร้างโค้ดใหม่ (refactor) เพื่อให้ทิศทางการไหลของข้อมูลมีความชัดเจนจากบนลงล่าง โดยอาศัย derived signal หรือ memo เป็นหลัก แต่หากจำเป็นต้องใช้จริง ๆ ในขอบเขตจำกัด ก็ยังไม่ใช่เรื่องคอขาดบาดตาย

> ผู้เขียนตั้งใจที่จะไม่ใส่ตัวอย่างโค้ดสำหรับกรณีนี้ไว้ที่นี่ หากต้องการศึกษาว่าทำงานอย่างไร สามารถอ่านได้จากเอกสารของ [`Effect`](https://docs.rs/leptos/latest/leptos/reactive/effect/struct.Effect.html)
